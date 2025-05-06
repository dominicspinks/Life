import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionMail,
    ionLockClosed,
    ionEye,
    ionEyeOff
} from '@ng-icons/ionicons';
import { SpinningIconComponent } from '../../../shared/icons/spinning-icon/spinning-icon.component';
import { ToastService } from '../../../shared/ui/toast/toast.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        RouterLink,
        NgIcon,
        SpinningIconComponent
    ],
    templateUrl: './register.component.html',
    providers: [
        provideIcons({
            ionMail,
            ionLockClosed,
            ionEye,
            ionEyeOff
        }),
    ]
})
export class RegisterComponent {
    private formBuilder = inject(FormBuilder);
    private authService = inject(AuthService);
    private router = inject(Router);
    private toastService = inject(ToastService);

    registerForm!: FormGroup;
    isLoading = false;
    hidePassword = true;
    hideConfirmPassword = true;

    ngOnInit(): void {
        this.registerForm = this.formBuilder.group({
            email: ['', [Validators.required, Validators.email]],
            password: ['', [Validators.required, Validators.minLength(8)]],
            confirmPassword: ['', [Validators.required]]
        }, { validators: this.passwordMatchValidator });
    }

    // Custom validator to check if passwords match
    passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
        const password = control.get('password')?.value;
        const confirmPassword = control.get('confirmPassword')?.value;

        // If either field is empty, let the required validator handle it
        if (!password || !confirmPassword) {
            return null;
        }

        // Only return an error when passwords don't match
        return password === confirmPassword ? null : { passwordMismatch: true };
    }

    onSubmit(): void {
        if (this.registerForm.invalid) {
            return;
        }

        this.isLoading = true;
        const { email, password } = this.registerForm.value;

        this.authService.register(email, password).subscribe({
            next: () => {
                this.router.navigate(['/login']);
            },
            error: (error) => {
                this.isLoading = false;
                if (error.status === 400 && error.error?.email?.length > 0) {
                    this.toastService.show('An account with this email already exists.', 'error', 3000);
                } else {
                    this.toastService.show('An error occurred during registration.', 'error', 3000);
                }
            },
            complete: () => {
                this.isLoading = false;
            }
        });
    }
}