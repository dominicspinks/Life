import { Component, input, output } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionClose,
} from '@ng-icons/ionicons';

@Component({
    selector: 'app-modal',
    standalone: true,
    imports: [NgIcon],
    templateUrl: './modal.component.html',
    providers: [provideIcons({
        ionClose
    })],
})
export class ModalComponent {
    show = input.required<boolean>();
    title = input('');
    closed = output<void>();

    close(): void {
        console.log("close")
        this.closed.emit();
    }
}
