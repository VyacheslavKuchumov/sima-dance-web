if __name__ == "__main__":
    import uvicorn
    PORT = 3000
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, proxy_headers=True, forwarded_allow_ips="*")