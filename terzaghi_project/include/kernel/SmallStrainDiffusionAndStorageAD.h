#pragma once

#include "ADTimeKernel.h"

class SmallStrainDiffusionAndStorageAD : public ADTimeKernel
{
public:
  static InputParameters validParams();
  SmallStrainDiffusionAndStorageAD(const InputParameters & params);

protected:
  virtual ADReal computeQpResidual() override;

  const Real _kappa_mu;
  const Real _m_v;
};