import { createRouter, createWebHistory } from 'vue-router'

import ThronePage from '../pages/ThronePage.vue'
import CampaignPage from '../pages/CampaignPage.vue'
import SectionPage from '../pages/SectionPage.vue'
import LessonPage from '../pages/LessonPage.vue'
import PracticePage from '../pages/PracticePage.vue'
import CodexPage from '../pages/CodexPage.vue'
import VulgarLibraryPage from '../pages/VulgarLibraryPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'throne', component: ThronePage },
    { path: '/campaign', name: 'campaign', component: CampaignPage },
    { path: '/section/:sectionId', name: 'section', component: SectionPage },
    { path: '/lesson/:lessonId', name: 'lesson', component: LessonPage },
    { path: '/practice', name: 'practice', component: PracticePage },
    { path: '/codex', name: 'codex', component: CodexPage },
    { path: '/vulgar', name: 'vulgar', component: VulgarLibraryPage },
    { path: '/profile', name: 'profile', component: ProfilePage },
  ],
})
