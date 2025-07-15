pipeline {
    agent any

    environment {
        APP_NAME = 'stocksight-backend'
        VENV_PATH = "${WORKSPACE}/venv/Scripts/activate"
        MAIN_FILE = 'app/main.py'
        JENKINS_NODE_COOKIES = 'dontKillMe'
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
                    pm2 delete ${APP_NAME} || true
                    export PYTHONPATH=$WORKSPACE
                    pm2 start ${MAIN_FILE} --name ${APP_NAME} --interpreter python3 --cwd $WORKSPACE
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