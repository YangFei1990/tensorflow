# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Contains Gradient functions for image ops."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import gen_image_ops


@ops.RegisterGradient("ResizeNearestNeighbor")
def _ResizeNearestNeighborGrad(op, grad):
  """The derivatives for nearest neighbor resizing.

  Args:
    op: The ResizeNearestNeighbor op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input and the output.
  """
  image = op.inputs[0]
  if image.get_shape()[1:3].is_fully_defined():
    image_shape = image.get_shape()[1:3]
  else:
    image_shape = array_ops.shape(image)[1:3]

  grads = gen_image_ops.resize_nearest_neighbor_grad(
      grad,
      image_shape,
      align_corners=op.get_attr("align_corners"),
      half_pixel_centers=op.get_attr("half_pixel_centers"))
  return [grads, None]


@ops.RegisterGradient("ResizeBilinear")
def _ResizeBilinearGrad(op, grad):
  """The derivatives for bilinear resizing.

  Args:
    op: The ResizeBilinear op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input.
  """
  grad0 = gen_image_ops.resize_bilinear_grad(
      grad,
      op.inputs[0],
      align_corners=op.get_attr("align_corners"),
      half_pixel_centers=op.get_attr("half_pixel_centers"))
  return [grad0, None]


@ops.RegisterGradient("ScaleAndTranslate")
def _ScaleAndTranslateGrad(op, grad):
  """The derivatives for ScaleAndTranslate transformation op.

  Args:
    op: The ScaleAndTranslate op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input.
  """

  grad0 = gen_image_ops.scale_and_translate_grad(
      grad,
      op.inputs[0],
      op.inputs[2],
      op.inputs[3],
      kernel_type=op.get_attr("kernel_type"),
      antialias=op.get_attr("antialias"))
  return [grad0, None, None, None]


@ops.RegisterGradient("ResizeBicubic")
def _ResizeBicubicGrad(op, grad):
  """The derivatives for bicubic resizing.

  Args:
    op: The ResizeBicubic op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input.
  """
  allowed_types = [dtypes.float32, dtypes.float64]
  grad0 = None
  if op.inputs[0].dtype in allowed_types:
    grad0 = gen_image_ops.resize_bicubic_grad(
        grad,
        op.inputs[0],
        align_corners=op.get_attr("align_corners"),
        half_pixel_centers=op.get_attr("half_pixel_centers"))
  return [grad0, None]


@ops.RegisterGradient("CropAndResize")
def _CropAndResizeGrad(op, grad):
  """The derivatives for crop_and_resize.

  We back-propagate to the image only when the input image tensor has floating
  point dtype but we always back-propagate to the input boxes tensor.

  Args:
    op: The CropAndResize op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input image, boxes, as well as the always-None
    gradients w.r.t. box_ind and crop_size.
  """
  image = op.inputs[0]
  if image.get_shape().is_fully_defined():
    image_shape = image.get_shape().as_list()
  else:
    image_shape = array_ops.shape(image)

  allowed_types = [dtypes.float16, dtypes.float32, dtypes.float64]
  if op.inputs[0].dtype in allowed_types:
    # pylint: disable=protected-access
    grad0 = gen_image_ops.crop_and_resize_grad_image(
        grad, op.inputs[1], op.inputs[2], image_shape, T=op.get_attr("T"),
        method=op.get_attr("method"))
    # pylint: enable=protected-access
  else:
    grad0 = None

  # `grad0` is the gradient to the input image pixels and it
  # has been implemented for nearest neighbor and bilinear sampling
  # respectively. `grad1` is the gradient to the input crop boxes' coordinates.
  # When using nearest neighbor sampling, the gradient to crop boxes'
  # coordinates are not well defined. In practice, we still approximate
  # grad1 using the gradient derived from bilinear sampling.
  grad1 = gen_image_ops.crop_and_resize_grad_boxes(
      grad, op.inputs[0], op.inputs[1], op.inputs[2])

  return [grad0, grad1, None, None]

@ops.RegisterGradient("ROIAlign")
def _ROIAlignGrad(op, grad):
  """The derivatives for ROIAlign.

  Args:
    op: The ROIAlign op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input features and always-None
    gradients w.r.t. rois.
  """
  original_input = op.inputs[0]
  rois = op.inputs[1]

  #allowed_types = [dtypes.float16, dtypes.float32, dtypes.float64]
  allowed_types = [dtypes.float32]
  if op.inputs[0].dtype in allowed_types:
    # pylint: disable=protected-access
    grad0 = gen_roi_align_op.roi_align_v2_grad(
        grad, original_input, rois,
        spatial_scale=op.get_attr("spatial_scale"),
        pooled_height=op.get_attr("pooled_height"),
        pooled_width=op.get_attr("pooled_width"),
        sampling_ratio=op.get_attr("sampling_ratio"),
        min_level=op.get_attr("min_level"),
        max_level=op.get_attr("max_level"),
        canonical_scale=op.get_attr("canonical_scale"),
        canonical_level=op.get_attr("canonical_level"),
        debug=op.get_attr("debug"),
        )
    # pylint: enable=protected-access
  else:
    grad0 = None
  # gradient wrt rois is 0
  return [grad0, None]
