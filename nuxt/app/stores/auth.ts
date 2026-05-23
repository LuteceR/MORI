export const useAuthStore = defineStore('auth', () => {
    const user = ref<any>(null);

    const isAuthenticated = computed(() => !!user.value);

    const fetchUser = async () => {
        try {
            const response = await fetch('http://localhost:8000/me',
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