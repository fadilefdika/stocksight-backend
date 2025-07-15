pipeline {
    agent any

    environment {
        APP_NAME = 'stocksight-backend'
        VENV_PATH = "${WORKSPACE}/venv/Scripts/activate"
        MAIN_FILE = 'app/main.py'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/Scripts/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Stop Previous App') {
            steps {
                sh '''
                    pm2 stop ${APP_NAME} || true
                    pm2 delete ${APP_NAME} || true
                '''
            }
        }
        stage('Start App with PM2') {
            steps {
                sh '''
                    . venv/Scripts/activate
                    pm2 start ${MAIN_FILE} --name ${APP_NAME} --interpreter python3
                '''
            }
        }
        stage('Save PM2 Process List') {
            steps {
                sh 'pm2 save'
            }
        }
    }
}