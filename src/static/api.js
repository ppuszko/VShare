const API_BASE_URL = "http://localhost:8000";

let isRefreshing = false;
let refreshSubscribers = [];

// Helper to notify all pending requests once refresh is done
function onTokenRefreshed(newAccessToken) {
    refreshSubscribers.map((callback) => callback(newAccessToken));
    refreshSubscribers = [];
}

export async function apiRequest(endpoint, options = {}) {
    const getHeaders = (token) => ({
        "Content-Type": "application/json",
        ...(token && { "Authorization": `Bearer ${token}` }),
        ...options.headers,
    });

    let currentToken = localStorage.getItem("accessToken");

    try {
        let response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            body: typeof options.body === 'object' ? JSON.stringify(options.body) : options.body,
            headers: getHeaders(currentToken),
            credentials: "include",
        });

        if (response.status === 401) {
            // If we are already refreshing, wait for it to finish
            if (isRefreshing) {
                return new Promise((resolve) => {
                    refreshSubscribers.push((newToken) => {
                        resolve(fetch(`${API_BASE_URL}${endpoint}`, {
                            ...options,
                            headers: getHeaders(newToken),
                            credentials: "include",
                        }));
                    });
                });
            }

            // Start the refresh process
            isRefreshing = true;
            console.log("Token expired, attempting singleton refresh...");

            const refreshRes = await fetch(`${API_BASE_URL}/refresh`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            });

            if (refreshRes.ok) {
                const data = await refreshRes.json();
                const newAccessToken = data.access_token;
                
                localStorage.setItem("accessToken", newAccessToken);
                isRefreshing = false;

                // Notify all other 401'd requests
                onTokenRefreshed(newAccessToken);

                // Retry THIS original request
                return await fetch(`${API_BASE_URL}${endpoint}`, {
                    ...options,
                    headers: getHeaders(newAccessToken),
                    credentials: "include",
                });
            } else {
                // ONLY clear storage and redirect if the REFRESH itself fails
                isRefreshing = false;
                localStorage.removeItem("accessToken");
                console.error("Session expired. Redirecting...");
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