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
  triggers {
    pollSCM('H/1 * * * *')
  }

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

    stage('Trivy Scan (Repo + Imagen)') {
      steps {
        sh '''
          set -e
          mkdir -p "${REPORTS_DIR}"
          mkdir -p .trivycache

          echo "=== 1) Scan del REPO (fs) -> reportes (NO falla aquí) ==="
          docker run --rm \
            -v "$PWD:/work" -w /work \
            -v "$PWD/.trivycache:/root/.cache/" \
            -v "$PWD/${REPORTS_DIR}:/out" \
            aquasec/trivy:latest fs \
            --scanners vuln,misconfig,secret \
            --severity HIGH,CRITICAL \
            --format sarif -o /out/trivy-fs.sarif \
            .

          docker run --rm \
            -v "$PWD:/work" -w /work \
            -v "$PWD/.trivycache:/root/.cache/" \
            -v "$PWD/${REPORTS_DIR}:/out" \
            aquasec/trivy:latest fs \
            --scanners vuln,misconfig,secret \
            --severity HIGH,CRITICAL \
            --format template --template "@contrib/html.tpl" \
            -o /out/trivy-fs.html \
            .

          echo "=== 2) Scan de la IMAGEN -> reportes (NO falla aquí) ==="
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD/.trivycache:/root/.cache/" \
            -v "$PWD/${REPORTS_DIR}:/out" \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --format sarif -o /out/trivy-image.sarif \
            "${IMAGE_TAG}"

          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$PWD/.trivycache:/root/.cache/" \
            -v "$PWD/${REPORTS_DIR}:/out" \
            aquasec/trivy:latest image \
            --severity HIGH,CRITICAL \
            --format template --template "@contrib/html.tpl" \
            -o /out/trivy-image.html \
            "${IMAGE_TAG}"

          echo "=== 3) Quality Gate (falla si hay HIGH/CRITICAL) ==="
          # Gate por imagen (SO base + libs)
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
      archiveArtifacts artifacts: "${REPORTS_DIR}/**", allowEmptyArchive: true
    }
  }
}
