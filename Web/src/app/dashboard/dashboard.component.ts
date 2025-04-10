// src/app/dashboard/dashboard.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../auth/auth.service';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [
        CommonModule,
        MatToolbarModule,
        MatButtonModule
    ],
    template: `
    <mat-toolbar color="primary">
      <span>My App Dashboard</span>
      <span style="flex: 1 1 auto;"></span>
      <button mat-button (click)="logout()">Logout</button>
    </mat-toolbar>
    <div style="padding: 20px;">
      <h1>Welcome to the Dashboard</h1>
      <p>You're logged in successfully!</p>
    </div>
  `,
    styles: [`
    .spacer {
      flex: 1 1 auto;
    }
  `]
})
export class DashboardComponent {
    constructor(private authService: AuthService) { }

    logout(): void {
        this.authService.logout().subscribe();
    }
}