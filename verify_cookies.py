import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8000"

async def test_cookie_auth():
    print("Testing Cookie-Based Auth Flow...")
    
    # 1. Login
    async with httpx.AsyncClient() as client:
        # Register/Login to get cookies
        email = "cookieuser@example.com"
        password = "secretpassword"
        
        # Try login first
        print("- Logging in...")
        response = await client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if response.status_code == 400:
             # Register if failed
             print("- Registering...")
             response = await client.post(f"{BASE_URL}/auth/register", json={"name": "Cookie User", "email": email, "password": password})
        
        assert response.status_code == 200
        cookies = response.cookies
        print(f"✅ Login successful. Cookies received: {list(cookies.keys())}")
        assert "access_token" in cookies
        assert "refresh_token" in cookies

        # 2. Access Protected Route (Analyze) with Cookies
        print("- accessing /analyze (Authenticated)...")
        # Note: client keeps cookies automatically in context
        response = await client.post(
            f"{BASE_URL}/analyze/", 
            json={"text": "This is a test claim for cookie auth."},
            cookies=cookies # Explicitly passing to be sure, though AsyncClient handles it
        )
        assert response.status_code == 200
        print("✅ Analyze request successful (Authenticated)")
        
        # 3. Refresh Token
        print("- Refreshing token...")
        response = await client.post(f"{BASE_URL}/auth/refresh", cookies=cookies)
        assert response.status_code == 200
        new_cookies = response.cookies
        print(f"✅ Refresh successful. New access token received? {'access_token' in new_cookies}")
        assert "access_token" in new_cookies
        
        # Update cookies map
        cookies.update(new_cookies)

        # 4. Logout
        print("- Logging out...")
        response = await client.post(f"{BASE_URL}/auth/logout")
        assert response.status_code == 200
        
        # Verify cookies are cleared (headers Set-Cookie with max-age=0 or expires)
        print("✅ Logout successful.")
        
        # 5. Access Protected Route again (Should be anonymous / no user)
        # We can't easily check "no user" on analyze since it supports anon, 
        # but we can check /auth/me which requires auth
        
        print("- Checking /auth/me after logout (Expect 401)...")
        response = await client.get(f"{BASE_URL}/auth/me")
        assert response.status_code == 401
        print("✅ Correctly rejected unauthenticated request.")

if __name__ == "__main__":
    asyncio.run(test_cookie_auth())
