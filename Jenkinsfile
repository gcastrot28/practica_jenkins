// pipeline {
//     agent any 
//     stages {
//         stage('Build') { 
//             steps {
//                 echo 'Construyendo la Aplicación' 
//             }
//         }
//         stage('Test') { 
//             steps {
//                 echo 'Arranca el proceso de pruebas unitarias' 
//             }
//         }
//         stage('Deploy') { 
//             steps {
//                 echo 'Desplegando al área de desarrollo' 
//             }
//         }
//     }
// }
// pipeline {
//   agent any
//   triggers {
//     pollSCM('* * * * *')
//   }
//   stages {
//     stage('Checkout') {
//       steps {
//         checkout scm
//       }
//     }
//     stage('Build') {
//       steps {
//         echo "Build..."
//       }
//     }
//   }
// }


// pipeline {
//   agent any
//   triggers {
//     pollSCM('H/1 * * * *')
//   }
//   stages {
//     stage('Verificación SCM') {
//       steps {
//         checkout scm
//         script {
//           env.GIT_COMMIT_SHORT = sh(
//             script: "git rev-parse --short HEAD",
//             returnStdout: true
//           ).trim()
//         }
//       }
//     }
//     stage('Docker Build & Push') {
//       steps {
//         script {
//           docker.withRegistry('https://registry.hub.docker.com', 'docker-hub') {
//             def nuestraapp = docker.build("lancelot2714/pythonapp:${env.GIT_COMMIT_SHORT}", ".")
//             nuestraapp.push()
//           }
//         }
//       }
//     }
//   }
// }

pipeline {
  agent any
  triggers { pollSCM('H/1 * * * *') }

  environment {
    DOCKER_IMAGE_REPO = "lancelot2714/pythonapp"
    REPORTS_DIR = "reports"
  }

  stages {
    stage('Verificación SCM') {
      steps {
        checkout scm
        script {
          env.GIT_COMMIT_SHORT = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
          ).trim()
          env.IMAGE_TAG = "${env.DOCKER_IMAGE_REPO}:${env.GIT_COMMIT_SHORT}"
        }
      }
    }

    stage('Docker Build (local)') {
      steps {
        script {
          docker.build(env.IMAGE_TAG, ".")
        }
      }
    }

    stage('Trivy Scan (Imagen)') {
      steps {
        sh '''
          set -e
          mkdir -p .trivycache
          mkdir -p "${REPORTS_DIR}"

          echo "========================================================"
          echo " Trivy scan de IMAGEN: ${IMAGE_TAG}"
          echo " (Consulta el resultado completo en: Jenkins > Console Output)"
          echo "========================================================"

          echo "=== 1) ESCANEO (salida en consola) ==="
          # Esto SIEMPRE corre y muestra resultados en el log.
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD/.trivycache:/root/.cache/" \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --format table \
            "${IMAGE_TAG}" || true

          echo "=== 2) Intento de generar reportes (si falla, NO falla el pipeline) ==="
          set +e

          # SARIF (para herramientas)
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD/.trivycache:/root/.cache/" \
            -v "$PWD/${REPORTS_DIR}:/out" \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --format sarif \
            -o /out/trivy-image.sarif \
            "${IMAGE_TAG}"
          SARIF_RC=$?

          # TXT (table guardado)
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD/.trivycache:/root/.cache/" \
            -v "$PWD/${REPORTS_DIR}:/out" \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --format table \
            -o /out/trivy-image.txt \
            "${IMAGE_TAG}"
          TXT_RC=$?

          set -e

          if [ $SARIF_RC -ne 0 ] && [ $TXT_RC -ne 0 ]; then
            echo "⚠️  No se pudo generar SARIF/TXT. No pasa nada: revisa el resultado en Console Output."
          else
            echo "✅ Reportes generados (los verás en Jenkins > Artifacts):"
            [ $SARIF_RC -eq 0 ] && echo " - ${REPORTS_DIR}/trivy-image.sarif"
            [ $TXT_RC -eq 0 ] && echo " - ${REPORTS_DIR}/trivy-image.txt"
          fi

          echo "=== 3) Quality Gate (falla si hay HIGH/CRITICAL) ==="
          # Si quieres que NO bloquee el pipeline, cambia --exit-code 1 por --exit-code 0
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD/.trivycache:/root/.cache/" \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --exit-code 1 \
            "${IMAGE_TAG}"

          echo "✅ Gate OK (sin HIGH/CRITICAL)"
        '''
      }
    }

    stage('Docker Push') {
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', 'docker-hub') {
            docker.image(env.IMAGE_TAG).push()
          }
        }
      }
    }
  }

  post {
    always {
      // Archiva reportes si existen (si no existen, no falla)
      archiveArtifacts artifacts: "${REPORTS_DIR}/**", allowEmptyArchive: true

      echo "Cómo consultar resultados:"
      echo "1) Jenkins > tu build > Console Output (siempre disponible)"
      echo "2) Jenkins > tu build > Artifacts (si se generaron reportes)"
    }
  }
}
