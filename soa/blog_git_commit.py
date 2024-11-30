import subprocess
import datetime
import os

def check_changes():
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    return bool(result.stdout.strip())

def deploy_blog():
    try:
        os.chdir('user/dir/to/blog')

        if check_changes():
            subprocess.run(['git', 'add', '.'], check=True)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(['git', 'commit', '-m', f'Update blog: {timestamp}'], check=True)
            subprocess.run(['git', 'push'], check=True)
            return 'Changes deployed successfully'
        else:
            return "No changes to deploy"

    except subprocess.CalledProcessError as e:
        return str(f'Error: {e}')

if __name__ == '__main__':
    deploy_blog()
