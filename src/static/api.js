const API_BASE_URL = "http://localhost:8000";

let isRefreshing = false;
let refreshSubscribers = [];

function onTokenRefreshed(newAccessToken) {
    refreshSubscribers.map((callback) => callback(newAccessToken));
    refreshSubscribers = [];
}

export async function apiRequest(endpoint, options = {}) {
    const getHeaders = (token) => {
        const headers = { ...options.headers };
        if (token) headers["Authorization"] = `Bearer ${token}`;
        
        if (options.body && !(options.body instanceof FormData)) {
            headers["Content-Type"] = "application/json";
        }
        return headers;
    };

    let requestBody = options.body;
    if (requestBody && typeof requestBody === 'object' && !(requestBody instanceof FormData)) {
        requestBody = JSON.stringify(requestBody);
    }

    let currentToken = localStorage.getItem("accessToken");

    try {
        let fetchOptions = {
            ...options,
            body: requestBody,
            headers: getHeaders(currentToken),
            credentials: "include",
        };

        let response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);

        if (response.status === 403) {
            console.warn("Access forbidden or token invalid. Redirecting to login...");
            localStorage.removeItem("accessToken");
            window.location.href = "/static/sign-in.html";
            return null;
        }

        if (response.status === 401) {
            if (isRefreshing) {
                return new Promise((resolve) => {
                    refreshSubscribers.push((newToken) => {
                        fetchOptions.headers = getHeaders(newToken);
                        resolve(fetch(`${API_BASE_URL}${endpoint}`, fetchOptions));
                    });
                });
            }

            isRefreshing = true;
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
                onTokenRefreshed(newAccessToken);

                fetchOptions.headers = getHeaders(newAccessToken);
                return await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);
            } else {
                isRefreshing = false;
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