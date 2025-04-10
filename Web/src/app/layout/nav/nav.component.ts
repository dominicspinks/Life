import { Component } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';
import { RouterLink } from '@angular/router';
import { UserModuleMenu } from '../../core/models/userModule.model';

@Component({
    selector: 'app-nav',
    imports: [RouterLink,],
    templateUrl: './nav.component.html',
    styleUrl: './nav.component.css'
})
export class NavComponent {
    userEmail: string = '';
    isUserMenuOpen = false;
    isMobileMenuOpen = false;

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
}
