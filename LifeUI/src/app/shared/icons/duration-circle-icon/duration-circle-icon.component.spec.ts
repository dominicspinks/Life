import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DurationCircleIconComponent } from './duration-circle-icon.component';

describe('DurationCircleIconComponent', () => {
  let component: DurationCircleIconComponent;
  let fixture: ComponentFixture<DurationCircleIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DurationCircleIconComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DurationCircleIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
