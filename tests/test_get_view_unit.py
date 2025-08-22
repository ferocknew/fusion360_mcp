"""
get_view 功能的单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# 导入被测试的模块
from src.fusion360_mcp.view_tools import get_view
from src.fusion360_mcp.fusion360_api import get_api


class TestGetView:
    """get_view 功能的单元测试类"""

    @pytest.fixture
    def mock_api(self):
        """创建模拟的 API 实例"""
        api = MagicMock()
        api._request = AsyncMock()
        return api

    @pytest.fixture(autouse=True)
    def setup(self, mock_api):
        """每个测试前的设置"""
        # 模拟 get_api 函数返回模拟的 API 实例
        with patch('src.fusion360_mcp.view_tools.get_api', return_value=mock_api):
            self.mock_api = mock_api
            yield

    @pytest.mark.asyncio
    async def test_get_view_default_parameters(self):
        """测试使用默认参数调用 get_view"""
        # 设置模拟返回值
        expected_result = {
            "status": "success",
            "image_data": "base64_encoded_image_data",
            "format": "png",
            "width": 1920,
            "height": 1080
        }
        self.mock_api._request.return_value = expected_result

        # 调用被测试的函数
        result = await get_view()

        # 验证调用
        self.mock_api._request.assert_called_once_with(
            "GET",
            "/api/view",
            {
                "action": "get_view",
                "parameters": {
                    "camera_position": None,
                    "target_position": None,
                    "format": "png",
                    "width": 1920,
                    "height": 1080
                }
            }
        )

        # 验证结果
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_view_custom_parameters(self):
        """测试使用自定义参数调用 get_view"""
        # 准备测试数据
        camera_position = [10.0, 20.0, 30.0]
        target_position = [0.0, 0.0, 0.0]
        format_type = "jpg"
        width = 800
        height = 600

        expected_result = {
            "status": "success",
            "image_data": "custom_base64_data",
            "format": "jpg",
            "width": 800,
            "height": 600
        }
        self.mock_api._request.return_value = expected_result

        # 调用被测试的函数
        result = await get_view(
            camera_position=camera_position,
            target_position=target_position,
            format=format_type,
            width=width,
            height=height
        )

        # 验证调用
        self.mock_api._request.assert_called_once_with(
            "GET",
            "/api/view",
            {
                "action": "get_view",
                "parameters": {
                    "camera_position": camera_position,
                    "target_position": target_position,
                    "format": format_type,
                    "width": width,
                    "height": height
                }
            }
        )

        # 验证结果
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_view_partial_parameters(self):
        """测试使用部分自定义参数调用 get_view"""
        camera_position = [5.0, 10.0, 15.0]

        expected_result = {
            "status": "success",
            "image_data": "partial_custom_data"
        }
        self.mock_api._request.return_value = expected_result

        # 调用被测试的函数（只提供 camera_position）
        result = await get_view(camera_position=camera_position)

        # 验证调用
        self.mock_api._request.assert_called_once_with(
            "GET",
            "/api/view",
            {
                "action": "get_view",
                "parameters": {
                    "camera_position": camera_position,
                    "target_position": None,  # 应该是默认值
                    "format": "png",         # 应该是默认值
                    "width": 1920,           # 应该是默认值
                    "height": 1080           # 应该是默认值
                }
            }
        )

        # 验证结果
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_view_api_error(self):
        """测试 API 请求失败的情况"""
        # 设置模拟的异常
        self.mock_api._request.side_effect = Exception("API 连接失败")

        # 验证异常被正确抛出
        with pytest.raises(Exception, match="API 连接失败"):
            await get_view()

    @pytest.mark.asyncio
    async def test_get_view_invalid_format(self):
        """测试无效格式参数"""
        expected_result = {
            "status": "success",
            "image_data": "test_data",
            "format": "invalid"
        }
        self.mock_api._request.return_value = expected_result

        # 调用被测试的函数（传入无效格式）
        result = await get_view(format="invalid")

        # 验证调用（函数应该允许任何格式字符串）
        self.mock_api._request.assert_called_once_with(
            "GET",
            "/api/view",
            {
                "action": "get_view",
                "parameters": {
                    "camera_position": None,
                    "target_position": None,
                    "format": "invalid",
                    "width": 1920,
                    "height": 1080
                }
            }
        )

        # 验证结果
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_view_zero_dimensions(self):
        """测试零尺寸参数"""
        expected_result = {
            "status": "success",
            "image_data": "zero_size_data"
        }
        self.mock_api._request.return_value = expected_result

        # 调用被测试的函数（传入零尺寸）
        result = await get_view(width=0, height=0)

        # 验证调用
        self.mock_api._request.assert_called_once_with(
            "GET",
            "/api/view",
            {
                "action": "get_view",
                "parameters": {
                    "camera_position": None,
                    "target_position": None,
                    "format": "png",
                    "width": 0,
                    "height": 0
                }
            }
        )

        # 验证结果
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_view_negative_dimensions(self):
        """测试负数尺寸参数"""
        expected_result = {
            "status": "success",
            "image_data": "negative_size_data"
        }
        self.mock_api._request.return_value = expected_result

        # 调用被测试的函数（传入负数尺寸）
        result = await get_view(width=-100, height=-200)

        # 验证调用
        self.mock_api._request.assert_called_once_with(
            "GET",
            "/api/view",
            {
                "action": "get_view",
                "parameters": {
                    "camera_position": None,
                    "target_position": None,
                    "format": "png",
                    "width": -100,
                    "height": -200
                }
            }
        )

        # 验证结果
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_view_empty_response(self):
        """测试空响应"""
        self.mock_api._request.return_value = {}

        # 调用被测试的函数
        result = await get_view()

        # 验证结果
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_view_logging(self):
        """测试日志记录功能"""
        expected_result = {"status": "success"}
        self.mock_api._request.return_value = expected_result

        # 使用日志模拟
        with patch('src.fusion360_mcp.view_tools.logger') as mock_logger:
            result = await get_view()

            # 验证日志被调用
            mock_logger.info.assert_called_once_with("获取视图截图成功")

        # 验证结果
        assert result == expected_result


if __name__ == "__main__":
    # 如果直接运行此文件，执行所有测试
    pytest.main([__file__, "-v"])
