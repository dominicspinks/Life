import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionMail,
    ionLockClosed,
    ionEye,
    ionEyeOff
} from '@ng-icons/ionicons';
import { SpinningIconComponent } from '../../../layout/icons/spinning-icon/spinning-icon.component';

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
    loginForm: FormGroup;
    isLoading = false;
    hidePassword = true;

    constructor(
        private formBuilder: FormBuilder,
        private authService: AuthService,
        private router: Router
    ) {
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
            error: () => {
                this.isLoading = false;
            },
            complete: () => {
                this.isLoading = false;
            }
        });
    }
}