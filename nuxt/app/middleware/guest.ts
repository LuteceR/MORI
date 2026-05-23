export default defineNuxtRouteMiddleware(async () => {
    const auth = useAuthStore()

    if (!auth.user) {
        await auth.fetchUser();
    }

    if (auth.user) {
        return navigateTo('/')
    }
})