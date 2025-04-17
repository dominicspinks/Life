import { Component } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';
import { RouterLink } from '@angular/router';
import { UserModuleMenu } from '../../core/models/userModule.model';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionChevronDown,
    ionChevronUp,
    ionClose,
    ionMenu,
} from '@ng-icons/ionicons';

@Component({
    selector: 'app-nav',
    standalone: true,
    imports: [
        RouterLink,
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
    userEmail: string = '';
    isUserMenuOpen = false;
    isMobileMenuOpen = false;
    isSettingsMenuOpen = false;
    isMobileSettingsOpen = false;

    userModules: UserModuleMenu[] = [];

    constructor(private authService: AuthService) { }

    ngOnInit(): void {
        this.authService.getUserEmail().subscribe(email => {
            if (email) {
                this.userEmail = email;
            }
        });
    }

    logout(): void {
        this.authService.logout().subscribe({
            next: () => console.log("logout success"),
            error: (err) => console.error("logout error", err),
        });
    }

    toggleUserMenu(setting?: boolean): void {
        this.isUserMenuOpen = setting ?? !this.isUserMenuOpen;
    }

    toggleSettingsMenu(setting?: boolean): void {
        this.isSettingsMenuOpen = setting ?? !this.isSettingsMenuOpen;
    }
}
