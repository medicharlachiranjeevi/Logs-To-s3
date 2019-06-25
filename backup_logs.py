import boto3
import datetime
import os
import configparser
class s3_upload:

    def __init__(self,bucket_name,destinaton_path):
        self.bucket_name=bucket_name
        self.destinaton_path='production/'+destinaton_path

    def access_log(self,path):
           files=os.listdir(path)
           for i in files:
               if 'gz' in i and 'access' in i:
                   result=self.upload(path+i,'nginx_access_log',self.bucket_name,self.destinaton_path)
                   print(result)

    def error_log(self,path):
           files=os.listdir(path)
           for i in files:
               if 'gz' in i and 'error' in i:
                   result=self.upload(str(path+i),'nginx_error_log',self.bucket_name,self.destinaton_path)

    def production_log(self,path):
           files=os.listdir(path)
           for i in files:
               if 'gz' in i and 'production' in i:
                   result=self.upload(path+i,'rails_production',self.bucket_name,self.destinaton_path)
    def data_base(self,username,password,host,database):
        os.system('export PGPASSWORD='+password+' ; pg_dump -U '+username+' -h '+host+' -d '+database+' | gzip > database.pgsql.gz')
        result=self.upload('database.pgsql.gz','database',self.bucket_name,self.destinaton_path)
    
    def upload(self,file,log_type,bucket_name,destinaton_path):
        s3 = boto3.client('s3')
        now = datetime.datetime.now()
        if 'pgsql' in file:
            filename=str(now.strftime('%Y-%m-%d-%H:%M:%S'))+'.sql.gz'
        else:
            filename=str(now.strftime('%Y-%m-%d-%H:%M:%S'))+'.log.gz'
        path=str(destinaton_path+"/"+log_type+"/"+filename)
        s3.upload_file(file,str(bucket_name),path)
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(bucket_name)
        test=[]
        for obj in my_bucket.objects.filter(Prefix=destinaton_path+'/'+log_type+'/'):
            test=test+[obj.key]
        if  destinaton_path+'/'+log_type+'/'+filename in test:
            os.system('sudo rm '+file)
            return True
        else:
            return False


def main():
    config = configparser.ConfigParser()
    config.read('files.config')
    server=config['server']['name']
    bucket_name=config['bucket']['name']
    s3_file_upload =s3_upload(bucket_name,server)
    s3_file_upload.access_log(config['logs']['nginx_path'])
    s3_file_upload.error_log(config['logs']['nginx_path'])
    s3_file_upload.production_log(config['logs']['application_path'])
    s3_file_upload.data_base(config['database']['username'],config['database']['password'],config['database']['host'],config['database']['database'])


if __name__=='__main__':
    main()
