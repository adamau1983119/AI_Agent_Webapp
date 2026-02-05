#!/bin/bash

# Elasticsearch IK Analyzer 安裝腳本
# 使用方法: ./install_ik_analyzer.sh [elasticsearch_version]

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 獲取 Elasticsearch 版本
ES_VERSION=${1:-"8.11.0"}
ES_HOST=${ES_HOST:-"http://localhost:9200"}

echo -e "${GREEN}=== Elasticsearch IK Analyzer 安裝腳本 ===${NC}"
echo -e "Elasticsearch 版本: ${YELLOW}${ES_VERSION}${NC}"
echo -e "Elasticsearch 主機: ${YELLOW}${ES_HOST}${NC}"
echo ""

# 檢查 Elasticsearch 是否運行
echo -e "${YELLOW}檢查 Elasticsearch 連接...${NC}"
if curl -s "${ES_HOST}" > /dev/null; then
    echo -e "${GREEN}✅ Elasticsearch 連接成功${NC}"
    
    # 獲取實際版本
    ACTUAL_VERSION=$(curl -s "${ES_HOST}" | grep -oP '"number"\s*:\s*"\K[^"]+')
    if [ ! -z "$ACTUAL_VERSION" ]; then
        echo -e "檢測到 Elasticsearch 版本: ${YELLOW}${ACTUAL_VERSION}${NC}"
        ES_VERSION=$ACTUAL_VERSION
    fi
else
    echo -e "${RED}❌ 無法連接到 Elasticsearch${NC}"
    echo -e "${YELLOW}請確保 Elasticsearch 正在運行，或設置 ES_HOST 環境變數${NC}"
    exit 1
fi

# 檢查 IK Analyzer 是否已安裝
echo -e "\n${YELLOW}檢查 IK Analyzer 是否已安裝...${NC}"
PLUGINS=$(curl -s "${ES_HOST}/_cat/plugins" 2>/dev/null || echo "")
if echo "$PLUGINS" | grep -q "analysis-ik"; then
    echo -e "${GREEN}✅ IK Analyzer 已安裝${NC}"
    echo -e "${YELLOW}如需重新安裝，請先卸載: bin/elasticsearch-plugin remove analysis-ik${NC}"
    exit 0
else
    echo -e "${YELLOW}IK Analyzer 未安裝，開始安裝...${NC}"
fi

# 構建下載 URL
IK_VERSION=$ES_VERSION
IK_URL="https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${IK_VERSION}/elasticsearch-analysis-ik-${IK_VERSION}.zip"

echo -e "\n${YELLOW}下載 URL: ${IK_URL}${NC}"

# 提示用戶手動安裝
echo -e "\n${YELLOW}=== 安裝步驟 ===${NC}"
echo -e "1. 進入 Elasticsearch 安裝目錄"
echo -e "2. 執行以下命令："
echo -e ""
echo -e "${GREEN}bin/elasticsearch-plugin install ${IK_URL}${NC}"
echo -e ""
echo -e "3. 重啟 Elasticsearch"
echo -e ""
echo -e "4. 驗證安裝："
echo -e "${GREEN}bin/elasticsearch-plugin list${NC}"
echo -e ""
echo -e "5. 測試分詞："
echo -e "${GREEN}curl -X POST \"${ES_HOST}/_analyze\" -H 'Content-Type: application/json' -d'{\"analyzer\": \"ik_max_word\", \"text\": \"中華人民共和國\"}'${NC}"

# 如果是 Docker 環境，提供 Docker 安裝方法
if [ ! -z "$DOCKER_CONTAINER" ]; then
    echo -e "\n${YELLOW}=== Docker 安裝方法 ===${NC}"
    echo -e "在 Docker 容器中執行："
    echo -e "${GREEN}docker exec -it ${DOCKER_CONTAINER} bin/elasticsearch-plugin install ${IK_URL}${NC}"
    echo -e "然後重啟容器："
    echo -e "${GREEN}docker restart ${DOCKER_CONTAINER}${NC}"
fi

echo -e "\n${GREEN}=== 安裝指南完成 ===${NC}"

