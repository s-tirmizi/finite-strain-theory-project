#pragma once

#include "ADTimeKernel.h"

class LargeStrainBiotDivergenceAD : public ADTimeKernel
{
  public:
    static InputParameters validParams();
    LargeStrainBiotDivergenceAD(const InputParameters & p);  

  protected:
    virtual ADReal computeQpResidual() override;

  private:
    const Real _B;  ///< Biot coefficient 
    const ADVariableValue & _u_x_dot; ///< ∇(∂ₜuₓ) at all QPs
    const ADVariableValue & _u_y_dot; ///< ∇(∂ₜuᵧ) at all QPs
      // gradients of those time derivatives
    const ADVariableGradient & _grad_u_x_dot; ///< ∇(∂ₜuₓ)
    const ADVariableGradient & _grad_u_y_dot; ///< ∇(∂ₜuᵧ)
    // We need the spatial gradients to build the Deformation Gradient (F)
    const ADVariableGradient & _grad_ux;
    const ADVariableGradient & _grad_uy;
};
