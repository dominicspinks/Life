import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpinningIconComponent } from './spinning-icon.component';

describe('SpinningIconComponent', () => {
  let component: SpinningIconComponent;
  let fixture: ComponentFixture<SpinningIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SpinningIconComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SpinningIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
