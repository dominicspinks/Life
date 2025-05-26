import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionMail,
    ionLockClosed,
    ionEye,
    ionEyeOff
} from '@ng-icons/ionicons';
import { AuthService } from '@core/auth/auth.service';
import { SpinningIconComponent } from '@shared/icons/spinning-icon/spinning-icon.component';
import { ToastService } from '@shared/ui/toast/toast.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        RouterLink,
        NgIcon,
        SpinningIconComponent
    ],
    templateUrl: './login.component.html',
    providers: [
        provideIcons({
            ionMail,
            ionLockClosed,
            ionEye,
            ionEyeOff
        }),
    ]
})
export class LoginComponent {
    private formBuilder = inject(FormBuilder);
    private authService = inject(AuthService);
    private router = inject(Router);
    private toastService = inject(ToastService);

    loginForm!: FormGroup;
    isLoading = false;
    hidePassword = true;

    ngOnInit(): void {
        this.loginForm = this.formBuilder.group({
            email: ['', [Validators.required, Validators.email]],
            password: ['', Validators.required]
        });
    }

    onSubmit(): void {
        if (this.loginForm.invalid) {
            return;
        }

        this.isLoading = true;
        const { email, password } = this.loginForm.value;

        this.authService.login(email, password).subscribe({
            next: () => {
                this.router.navigate(['/dashboard']);
            },
            error: (error) => {
                this.isLoading = false;

                if (error.status === 401) {
                    this.toastService.show('Invalid email or password.', 'error', 3000);
                }
            },
            complete: () => {
                this.isLoading = false;
            }
        });
    }
}