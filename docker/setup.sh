# 停止并移除所有相关容器、网络、卷
docker compose down --volumes --remove-orphans

# 删除 docker-compose.yml 中涉及的镜像
docker compose config | awk '/image:/ { print $2 }' | xargs -r docker rmi -f

# 重新构建 + 不使用缓存
docker compose build --no-cache

# 以 detached 模式启动
docker compose up -d

# 连接到 dify_net 网络
docker network connect --alias nginx dify_net docker-nginx-1
docker network connect dify_net local_pdf_to_md

sudo docker logs -f docker-api-1