import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-edit-list-module',
    imports: [],
    templateUrl: './edit-list-module.component.html'
})
export class EditListModuleComponent {
    moduleId: number;

    constructor(private route: ActivatedRoute) {
        this.moduleId = Number(this.route.snapshot.paramMap.get('id'));
    }
}
