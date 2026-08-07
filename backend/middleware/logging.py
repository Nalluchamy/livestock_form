import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.logging import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.info(f"Req [{request_id}] {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            logger.info(f"Res [{request_id}] {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}ms")
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            logger.error(f"Err [{request_id}] {request.method} {request.url.path} - Exception: {exc} - Time: {process_time:.2f}ms")
            raise
