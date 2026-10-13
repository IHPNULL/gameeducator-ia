// Pipeline do servico de IA (B1 - Desafio 6, ADR-B1-006): independente da pipeline do Core.
// Bloqueia o deploy: testes (pytest), gate de cobertura (90%) e smoke do contrato HTTP na imagem final.
// Jenkins local: gameeducator-backend/jenkins (o job e criado por init.groovy.d/create-job.groovy).
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        skipDefaultCheckout()
    }

    parameters {
        string(name: 'DOCKER_REGISTRY', defaultValue: '', description: 'Docker registry host para publicar a imagem em main')
    }

    environment {
        COMPOSE_PROJECT_NAME = "gameeducator-ia-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Codigo-fonte') {
            steps {
                deleteDir()
                script {
                    if (env.LOCAL_SOURCES_ROOT) {
                        sh """
                            tar -C "${env.LOCAL_SOURCES_ROOT}/gameeducator-ia" \\
                                --exclude=.git --exclude=.venv --exclude=reports \\
                                -cf - . | tar -xf -
                        """
                    } else {
                        checkout scm
                    }
                    env.IMAGE_TAG = sh(returnStdout: true, script: '''
                        if [ -n "$GIT_COMMIT" ]; then echo "$GIT_COMMIT" | cut -c1-12; else echo "local-${BUILD_NUMBER}"; fi
                    ''').trim()
                }
            }
        }

        stage('IA: testes') {
            steps {
                sh "docker build -f docker/ia.Dockerfile --target test -t gameeducator-ia:${IMAGE_TAG}-test ."
                sh "docker run --name ${COMPOSE_PROJECT_NAME}-test gameeducator-ia:${IMAGE_TAG}-test"
            }
            post {
                always {
                    sh "docker cp ${COMPOSE_PROJECT_NAME}-test:/app/reports reports || true"
                    sh "docker rm -f ${COMPOSE_PROJECT_NAME}-test || true"
                    junit testResults: 'reports/junit.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'reports/coverage.xml', allowEmptyArchive: true
                }
            }
        }

        stage('IA: imagem') {
            steps {
                sh "docker build -f docker/ia.Dockerfile --target runtime -t gameeducator-ia:${IMAGE_TAG} ."
            }
        }

        stage('IA: smoke do contrato') {
            // A imagem que sera publicada sobe e responde ao contrato que o Core consome.
            steps {
                sh "docker run -d --name ${COMPOSE_PROJECT_NAME}-smoke gameeducator-ia:${IMAGE_TAG}"
                sh """
                    ok=0
                    for i in \$(seq 1 30); do
                        if docker exec ${COMPOSE_PROJECT_NAME}-smoke python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/saude', timeout=2)" 2>/dev/null; then ok=1; break; fi
                        sleep 1
                    done
                    [ "\$ok" = "1" ] || { echo 'ERRO: servico de IA nao subiu' >&2; exit 1; }
                    docker exec ${COMPOSE_PROJECT_NAME}-smoke python -c "
import json, urllib.request
corpo = json.dumps({'alunoId': 1, 'cursoId': 1, 'missoes': [{'missaoId': 1, 'titulo': 'T', 'totalDesafios': 1, 'desafiosAcertados': 0, 'tentativas': 0, 'xpTotal': 10}]}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/recomendacoes', data=corpo, headers={'Content-Type': 'application/json'})
resposta = json.load(urllib.request.urlopen(req, timeout=5))
assert resposta['itens'][0]['missaoId'] == 1, resposta
print('contrato /recomendacoes OK:', resposta['modeloVersao'])
"
                """
            }
            post {
                always {
                    sh "docker rm -f ${COMPOSE_PROJECT_NAME}-smoke || true"
                }
            }
        }

        stage('Publish') {
            when { branch 'main' }
            steps {
                script {
                    if (!params.DOCKER_REGISTRY) {
                        echo 'DOCKER_REGISTRY nao configurado - pulando publicacao da imagem.'
                        return
                    }
                    docker.withRegistry("https://${params.DOCKER_REGISTRY}", 'gameeducator-docker-registry') {
                        sh "docker tag gameeducator-ia:${IMAGE_TAG} ${params.DOCKER_REGISTRY}/gameeducator-ia:${IMAGE_TAG}"
                        sh "docker push ${params.DOCKER_REGISTRY}/gameeducator-ia:${IMAGE_TAG}"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (env.IMAGE_TAG) {
                    sh "docker rmi gameeducator-ia:${env.IMAGE_TAG}-test || true"
                }
            }
        }
    }
}
