import axios from "axios";
import store from "@/store";


const instance = axios.create({
    baseURL: process.env.VUE_APP_SERVER,
    headers: {
        'Content-Type': 'application/json; charset = utf-8'
    }
})

instance.interceptors.request.use(
    function (config) {
        config.headers['x-access-token'] = localStorage.getItem('accessToken')
        return config;
    },
    function (error) {
        return Promise.reject(error);
    }
)
instance.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response.status == 403 && !error.config._retry) {
            await store.dispatch('auth/changeAccess')
            const _request = error.config
            _request._retry = true
            _request.headers['retry'] = true
            return instance(_request)
        }
        return Promise.reject(error);
    }
)
export default instance