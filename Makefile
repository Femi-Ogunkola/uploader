.PHONY: protos

build-protos:
	@ python3 -m grpc_tools.protoc -I=protos --python_out=server/stubs --grpc_python_out=server/stubs --pyi_out=server/stubs $(shell find protos -name "*.proto")

client-protos:
	@ protoc -I=protos protos/media.proto \
	--js_out=import_style=commonjs,binary:./client/generated \
	--grpc-web_out=import_style=commonjs,mode=grpcwebtext:./client/generated

start-server:
	@ cd server && python3 server.py

build-client:
	@ cd client && npm cache clean --force && rm -rf node_modules package-lock.json && npm install

start-client:
	@ cd client && node upload.js