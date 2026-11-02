pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t python-flask-app .'
            }
        }

        stage('Deploy Container') {
            steps {
                bat '''
                docker stop python-flask-container || echo Container not running
                docker rm python-flask-container || echo Container not found
                docker run -d -p 5000:5000 --name python-flask-container python-flask-app
                '''
            }
        }
    }
}
