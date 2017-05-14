echo "updating..."
apt update
echo "installing..."
apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile
pyenv install 3.6.1
sudo pyenv rehash
sudo pyenv global 3.6.1
git clone https://github.com/helloqiu/AsyncFTP --depth=1
cd AsyncFTP
pip install -r requirements.txt
python setup.py install
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
cd web-ui
npm i
npm run dev&
cd ..
python example.py
