export const useAuthStore = defineStore('auth', () => {
    const user = ref<any>(null);

    const isAuthenticated = computed(() => !!user.value);
    const apiBaseAuth = useRuntimeConfig().public.apiBaseAuth as string

    const fetchUser = async () => {
        try {
            const response = await fetch(new URL('/me', apiBaseAuth),
                {
                    credentials: 'include',
                }
            )
            
            user.value = await response.json();
        } catch {
            user.value = null;
        }
    }

    const setUser = (userData: any) => {
        user.value = userData;
    }

    return {
        user,
        setUser,
        isAuthenticated,
        fetchUser,
    };
});