import { Component, input } from '@angular/core';

@Component({
    selector: 'app-spinning-icon',
    standalone: true,
    imports: [],
    templateUrl: './spinning-icon.component.html',
    styleUrl: './spinning-icon.component.css'
})
export class SpinningIconComponent {
    colour = input<string>('');
    size = input<string>('');
}
