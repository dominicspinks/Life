import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToastMessageComponent } from './toast-message.component';

describe('MessageBubbleComponent', () => {
    let component: ToastMessageComponent;
    let fixture: ComponentFixture<ToastMessageComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ToastMessageComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(ToastMessageComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
