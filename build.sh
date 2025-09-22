cd frontend
pnpm build
# 判断 ../backend/public 是否存在
if [ ! -d "../backend/public" ]; then
  mkdir ../backend/public
# 如果存在先删除
else
  rm -rf ../backend/public
fi
cp -r dist ../backend/public