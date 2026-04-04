import { navigateTo } from "nuxt/app";

export default defineEventHandler(async (event) => {
    const body = await readBody(event);

    const sanitized = {
        username: body.login,
        password: body.password,
        rememberMe: body.rememberMe,
    }
    
    const res = await $fetch.raw('http://localhost:8000/authorization', {
        method: "POST",
        body: sanitized         
    });

    const cookies = res.headers.get('set-cookie');
    if (cookies) {
        setHeader(event, 'set-cookie', cookies);
    }

    return res._data
})