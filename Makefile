
project_name='huayu-storm'
nodejs_version=12.16.1
nodejs_filename=node-v$(nodejs_version)-win-x64
nodejs_url=https://npm.taobao.org/mirrors/node/v$(nodejs_version)/$(nodejs_filename).7z
nodejs_bin_dir=nodejs_bin
PATH=`pwd`/$(nodejs_bin_dir)/$(nodejs_filename):`pwd`/node_modules/.bin:/usr/bin:/mingw64/bin:/c/windows/system32/windowspowershell/v1.0:/c/windows/system32
PATH_WIN=%cd%/$(nodejs_bin_dir)/$(nodejs_filename);%cd%/node_modules/.bin;%GIT_INSTALL_ROOT%/mingw64/bin;c:/windows/system32/windowspowershell/v1.0;c:/windows/system32

help:
	echo help

write_bat:
	echo "set PATH=$(PATH_WIN)" > environ.bat

setup_nodejs:
	@mkdir $(nodejs_bin_dir) ;\
	pushd $(nodejs_bin_dir) ;\
		wget -O $(nodejs_version) $(nodejs_url) ;\
		7z x -y $(nodejs_version) ;\
		rm -f $(nodejs_version) ;\
	popd
	@make set_mirror_taobao
	@make write_bat

set_nodejs_env:
	@export PATH=$(PATH);\
		$(command)

find_electron:
	@make set_nodejs_env command='which electron'

set_mirror_taobao:
	command='npm config set registry http://registry.npm.taobao.org';\
 		make set_nodejs_env command="$${command}"

set_mirror_origin:
	command='npm config set registry http://registry.npmjs.org';\
 		make set_nodejs_env command="$${command}"

get_mirror:
	command='npm config get registry';\
 		make set_nodejs_env command="$${command}"

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
		npm run package ;\
	';
