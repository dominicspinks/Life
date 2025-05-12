import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';

export const routes: Routes = [
    {
        path: 'login',
        loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
    },
    {
        path: 'register',
        loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
    },
    {
        path: '',
        component: MainLayoutComponent,
        canActivate: [authGuard],
        children: [
            {
                path: 'modules',
                loadComponent: () =>
                    import('./features/manage-modules/manage-modules.component').then(m => m.ManageModulesComponent)
            },
            {
                path: 'modules/list/:id',
                loadComponent: () =>
                    import('./features/view-list-module/view-list-module.component').then(m => m.ViewListModuleComponent)
            },
            {
                path: 'modules/list/:id/edit',
                loadComponent: () =>
                    import('./features/edit-list-module/edit-list-module.component').then(m => m.EditListModuleComponent)
            },
            {
                path: 'modules/budget/:id',
                loadComponent: () =>
                    import('./features/budgets-page/budgets-page.component').then(m => m.BudgetsPageComponent),
                children: [
                    { path: '', redirectTo: 'summary', pathMatch: 'full' },
                    {
                        path: 'summary',
                        loadComponent: () =>
                            import('./features/budgets-page/tabs/budget-summary-tab/budget-summary-tab.component').then(m => m.BudgetSummaryTabComponent),
                    },
                    {
                        path: 'purchases',
                        loadComponent: () =>
                            import('./features/budgets-page/tabs/budget-purchases-tab/budget-purchases-tab.component').then(m => m.BudgetPurchasesTabComponent),
                    },
                    {
                        path: 'settings',
                        loadComponent: () =>
                            import('./features/budgets-page/tabs/budget-settings-tab/budget-settings-tab.component').then(m => m.BudgetSettingsTabComponent),
                    }
                ]
            },
            { path: '', redirectTo: '/modules', pathMatch: 'full' },
        ]
    },
    {
        path: '**',
        redirectTo: '/modules'
    }
];