
project_name='huayu-storm'
nodejs_version='12.16.1'
nodejs_filename=node-v$(nodejs_version)-win-x64
nodejs_url=https://npm.taobao.org/mirrors/node/v$(nodejs_version)/$(nodejs_filename).7z
nodejs_bin_dir=nodejs_bin

help:
	echo help

set_mirror_taobao:
	npm config set registry http://registry.npm.taobao.org

set_mirror_origin:
	npm config set registry http://registry.npmjs.org

get_mirror:
	npm config get registry

setup_nodejs:
	@mkdir $(nodejs_bin_dir) ;\
	pushd $(nodejs_bin_dir) ;\
		wget -O $(nodejs_version) $(nodejs_url) ;\
		7z x -y $(nodejs_version) ;\
		rm -f $(nodejs_version) ;\
	popd
	@make set_mirror_taobao
	echo 'set PATH=%cd%/$(nodejs_bin_dir)/$(nodejs_filename)' > nodejs_env.bat

set_nodejs_env:
	@export PATH=`pwd`/$(nodejs_bin_dir)/$(nodejs_filename):/usr/bin:/c/windows/system32;\
		$(command)

npm_run:
	@make set_nodejs_env command='$(command)'

del_app:
	@rm -rf $(project_name)

create_app:
	@make set_nodejs_env command=' \
		node -v;\
		npx create-react-app $(project_name) &&\
		mv $(project_name)/* ./ &&\
		npm install antd --save ;\
 	';

run_app:
	@make set_nodejs_env command=' \
		npm start ;\
 	';

run_app_electron:
	@make set_nodejs_env command=' \
		npm run start_electron;\
 	';

setup_deps:
	@make set_nodejs_env command=' \
		  npm i ;\
 	';

install_electron:
	@make set_nodejs_env command=' \
		npm install electron --save-dev;\
		npm install electron-packager --save-dev;\
 	';

run_flask:
	pushd engine ;\
		python engine.py

release:
	@make set_nodejs_env command=' \
		npm run package.json;\
	';
