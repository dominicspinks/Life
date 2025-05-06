import { Component, inject } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { UserModule, UserModuleMenu } from '../../core/models/userModule.model';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionChevronDown,
    ionChevronUp,
    ionClose,
    ionMenu,
} from '@ng-icons/ionicons';
import { ModuleService } from '../../core/services/module.service';
import { LoggerService } from '../../core/services/logger.service';

@Component({
    selector: 'app-nav',
    standalone: true,
    imports: [
        RouterLink,
        RouterLinkActive,
        NgIcon
    ],
    templateUrl: './nav.component.html',
    styleUrl: './nav.component.css',
    viewProviders: [provideIcons({
        ionChevronDown,
        ionChevronUp,
        ionClose,
        ionMenu
    })]
})
export class NavComponent {
    private moduleService = inject(ModuleService);
    private authService = inject(AuthService);
    private logger = inject(LoggerService);

    userEmail: string = '';
    isUserMenuOpen = false;
    isMobileMenuOpen = false;
    isSettingsMenuOpen = false;
    isMobileSettingsOpen = false;
    isListsMenuOpen = false;
    isBudgetsMenuOpen = false;

    activeLists: UserModuleMenu[] = [];
    activeBudgets: UserModuleMenu[] = [];

    ngOnInit(): void {
        this.authService.getUserEmail().subscribe(email => {
            if (email) {
                this.userEmail = email;
            }
        });

        this.moduleService.getUserModules(true).subscribe({
            next: (modules) => {
                this.activeLists = modules.results
                    .filter((m: UserModule) => m.module_name === 'list')
                    .filter((m: UserModule) => m.is_enabled)
                    .map((m: UserModule): UserModuleMenu => ({
                        id: m.id,
                        name: m.name
                    }));

                this.activeBudgets = modules.results
                    .filter((m: UserModule) => m.module_name === 'budget')
                    .filter((m: UserModule) => m.is_enabled)
                    .map((m: UserModule): UserModuleMenu => ({
                        id: m.id,
                        name: m.name
                    }));
            },
            error: (err) => this.logger.error('Failed to load user modules', err)
        });
    }

    logout(): void {
        this.authService.logout().subscribe({
            error: (err) => this.logger.error("logout error", err),
        });
    }

    toggleUserMenu(setting?: boolean): void {
        this.isUserMenuOpen = setting ?? !this.isUserMenuOpen;
    }

    toggleSettingsMenu(setting?: boolean): void {
        this.isSettingsMenuOpen = setting ?? !this.isSettingsMenuOpen;
    }

    toggleListMenu(setting?: boolean): void {
        this.isListsMenuOpen = setting ?? !this.isListsMenuOpen;
    }

    toggleBudgetsMenu(setting?: boolean): void {
        this.isBudgetsMenuOpen = setting ?? !this.isBudgetsMenuOpen;
    }
}
