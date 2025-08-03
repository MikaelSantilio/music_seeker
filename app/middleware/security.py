"""
Security middleware for MusicSeeker API
"""

from fastapi import Request
from fastapi.responses import JSONResponse
import time
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

# Configure security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança e logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Log suspicious patterns
        if self._is_suspicious_request(request):
            security_logger.warning(
                f"Suspicious request from {request.client.host}: {request.url}"
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """Detecta padrões suspeitos na requisição"""
        
        # Check for common attack patterns in URL
        suspicious_patterns = [
            "../", "etc/passwd", "cmd.exe", "powershell",
            "script>", "javascript:", "eval(", "union select",
            "drop table", "exec(", "<iframe"
        ]
        
        url_str = str(request.url).lower()
        for pattern in suspicious_patterns:
            if pattern in url_str:
                return True
        
        # Check User-Agent for common bot patterns
        user_agent = request.headers.get("user-agent", "").lower()
        bot_patterns = ["sqlmap", "nikto", "nmap", "masscan", "zap"]
        
        for pattern in bot_patterns:
            if pattern in user_agent:
                return True
        
        return False


async def add_process_time_header(request: Request, call_next: Callable):
    """Middleware para adicionar tempo de processamento"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def limit_request_size(request: Request, call_next: Callable):
    """Middleware para limitar tamanho de requisições"""
    content_length = request.headers.get("content-length")
    
    if content_length:
        content_length = int(content_length)
        # Limit to 1MB
        if content_length > 1024 * 1024:
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
    
    response = await call_next(request)
    return response
