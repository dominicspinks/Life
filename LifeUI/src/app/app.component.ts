import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ToastContainerComponent } from '@shared/ui/toast/toast-container/toast-container.component';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, ToastContainerComponent],
    templateUrl: './app.component.html'
})
export class AppComponent {
    title = 'Life';
}