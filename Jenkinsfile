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
pipeline {
  agent any
  triggers {
    pollSCM('H/2 * * * *')
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
        }
      }
    }
    stage('Docker Build & Push') {
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', 'docker-hub') {
            def nuestraapp = docker.build("lancelot2714/pythonapp:${env.GIT_COMMIT_SHORT}", ".")
            nuestraapp.push()
          }
        }
      }
    }
  }
}