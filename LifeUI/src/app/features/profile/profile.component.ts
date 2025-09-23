import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';
import { ProfileService } from '@core/services/profile.service';
import { DeleteModalComponent } from '@layout/delete-modal/delete-modal/delete-modal.component';

@Component({
    selector: 'app-profile',
    standalone: true,
    imports: [DeleteModalComponent],
    templateUrl: './profile.component.html',
    styleUrl: './profile.component.css',
})
export class ProfileComponent {
    private authService = inject(AuthService);
    private profileService = inject(ProfileService);
    private router = inject(Router);

    userEmail: string = '';
    showDeleteModal = false;

    ngOnInit(): void {
        this.authService.getUserEmail().subscribe((email) => {
            if (email) {
                this.userEmail = email;
            }
        });
    }
    confirmDeleteAccount() {
        this.showDeleteModal = true;
    }

    closeDeleteModal() {
        this.showDeleteModal = false;
    }

    deleteAccount() {
        this.profileService.deleteProfile().subscribe({
            next: () => {
                this.showDeleteModal = false;
                this.authService.logout().subscribe({
                    error: (err) => {
                        console.error('Error logging out:', err);
                        this.router.navigate(['/login']);
                    },
                });
            },
            error: (err) => {
                console.error('Error deleting profile:', err);
            },
        });
    }
}
