"""API 集成测试"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from src.api.main import app


@pytest.fixture
async def client():
    """创建测试客户端"""
    with patch("src.db.crud.db") as mock_db:
        mock_db.async_session = AsyncMock()
        mock_db.create_tables = AsyncMock()
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


class TestHealthCheck:
    """健康检查测试"""

    @pytest.mark.asyncio
    async def test_health(self, client):
        """测试健康检查端点"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """根端点测试"""

    @pytest.mark.asyncio
    async def test_root(self, client):
        """测试根端点"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["app_name"] == "Metis_ParseBot"


class TestStatusEndpoint:
    """状态端点测试"""

    @pytest.mark.asyncio
    async def test_status(self, client):
        """测试状态端点"""
        response = await client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


class TestCollectSources:
    """采集源测试"""

    @pytest.mark.asyncio
    async def test_list_sources(self, client):
        """测试获取采集源列表"""
        response = await client.get("/api/collect/sources")
        
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) > 0
        
        # 检查arxiv源
        arxiv = next((s for s in data["sources"] if s["name"] == "arxiv"), None)
        assert arxiv is not None
        assert arxiv["type"] == "academic"


class TestSchedulerEndpoints:
    """调度器端点测试"""

    @pytest.mark.asyncio
    async def test_get_jobs(self, client):
        """测试获取调度任务"""
        response = await client.get("/api/scheduler/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "is_running" in data


class TestContentsEndpoints:
    """内容端点测试"""

    @pytest.mark.asyncio
    async def test_list_contents_empty(self, client):
        """测试空内容列表"""
        with patch("src.api.routes.contents.CRUD.list_contents") as mock_list:
            mock_list.return_value = []
            
            response = await client.get("/api/contents")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"] == []

    @pytest.mark.asyncio
    async def test_get_content_not_found(self, client):
        """测试获取不存在的内容"""
        with patch("src.api.routes.contents.CRUD.get_content") as mock_get:
            mock_get.return_value = None
            
            response = await client.get("/api/contents/non-existent-id")
            
            assert response.status_code == 404


class TestPipelineEndpoint:
    """流水线端点测试"""

    @pytest.mark.asyncio
    async def test_pipeline_endpoint_exists(self, client):
        """测试流水线端点存在"""
        with patch("src.api.main.pipeline.run") as mock_run:
            mock_run.return_value = {
                "collect": None,
                "review": None,
                "analyze": None,
            }
            
            response = await client.post("/api/pipeline")
            
            assert response.status_code == 200