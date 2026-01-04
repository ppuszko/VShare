const API_BASE_URL = "http://localhost:8000";

export async function apiRequest(endpoint, options = {}) {
    let token = localStorage.getItem("accessToken");
    
    // 1. Prepare headers
    const headers = {
        "Content-Type": "application/json",
        ...(token && { "Authorization": `Bearer ${token}` }),
        ...options.headers,
    };

    try {
        // 2. Initial Request
        let response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });

        // 3. If Unauthorized (401), try to refresh the token
        if (response.status === 401) {
            console.log("Token expired, attempting silent refresh...");
            
            // We call the refresh endpoint. 
            // Note: If your refresh token is in an HttpOnly cookie, 
            // you must include credentials: 'include'
            const refreshRes = await fetch(`${API_BASE_URL}/refresh`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                // body: JSON.stringify({ refresh_token: localStorage.getItem("refreshToken") }) 
                // ^ Uncomment if you store refresh token in localStorage instead of cookies
            });

            if (refreshRes.ok) {
                const data = await refreshRes.json();
                
                // Save the new access token
                localStorage.setItem("accessToken", data.access_token);
                console.log("Token refreshed successfully.");

                // 4. RETRY the original request with the NEW token
                headers["Authorization"] = `Bearer ${data.access_token}`;
                response = await fetch(`${API_BASE_URL}${endpoint}`, {
                    ...options,
                    headers,
                });
            } else {
                // Refresh failed (refresh token also expired)
                console.warn("Refresh failed. Redirecting to login.");
                localStorage.removeItem("accessToken");
                window.location.href = "/static/sign-in.html";
                return null;
            }
        }

        return response;
    } catch (error) {
        console.error("Critical API Request Error:", error);
        return null;
    }
}