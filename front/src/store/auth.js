import router from '@/router'
import instance from "@/middlewares"
const checkStatuses = (status) => {
    switch (status) {
        case 400:
            window.alert('Проблема на клиенте?')
            return false
        case 404:
            window.alert('Пользователь не найден')
            return false
        case 414:
            window.alert('Пароль неверный')
            return false
        case 405:
            window.alert('Емайл уже используется')
            return false
        case 403:
            window.alert('Не авторизован')
            return false
        case 500:
            window.alert('Проблема на сервере')
            return false
        case 401:
            window.alert('Проблема с токеном')
            return false
        default: return true
    }
}

export default {
    name: 'auth',
    state: () => ({
        isAuth: false
    }),
    getters: {
    },
    mutations: {
        setAuth(state, isAuth) {
            state.isAuth = isAuth
        }
    },
    actions: {
        async register({ }, { email, password, name }) {
            const response = await fetch(`${process.env.VUE_APP_SERVER}/api/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-type': 'application/json; charset=utf-8'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    name: name
                })
            })
            if (!checkStatuses(response.status)) return
            window.alert('Вы были зарегистрированы')
            router.push('/login')
            return
        },
        async login({ commit }, { email, password }) {
            const response = await fetch(`${process.env.VUE_APP_SERVER}/api/auth/signin`, {
                method: 'POST',
                headers: { 'Content-type': 'application/json; charset=utf-8' },
                body: JSON.stringify({
                    email: email,
                    password: password,
                })
            })
            if (!checkStatuses(response.status)) return
            const result = await response.json()
            commit('setAuth', true)
            console.log(result)
            localStorage.setItem('accessToken', result.accessToken)
            localStorage.setItem('refreshToken', result.refreshToken)
            localStorage.setItem('uid', result.auth_uid)
            localStorage.setItem('username', result.username)
            router.push('/')
            return
        },
        async changeAccess({ }) {
            const response = await instance.post('/api/auth/changeAccess', {},  // Body data (empty in this case)
                {
                    headers: {
                        'x-refresh-token': localStorage.getItem('refreshToken')
                    }
                })
            if (!checkStatuses(response.status)) return
            localStorage.setItem('accessToken', response.data.accessToken)
            localStorage.setItem('refreshToken', response.data.refreshToken)
            return
        },
        logout ({commit}) {
            commit('setAuth', false)
            localStorage.removeItem ('uid')
            localStorage.removeItem ('accessToken')
            localStorage.removeItem ('refreshToken')
            localStorage.removeItem ('username')
            router.push('/login')
            return
        }
    },
    namespaced: true
}