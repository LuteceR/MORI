import jwt from 'jsonwebtoken'
import { defineNuxtRouteMiddleware, useState, navigateTo } from 'nuxt/app'

export default defineNuxtRouteMiddleware((to, from) => {
    const auth = useState('auth')

    if (!auth.value.isAuthenticated) {
        return navigateTo('/login')
    }

    if (to.path !== '/dashboard') {
        return navigateTo('/dashboard')
    }
})