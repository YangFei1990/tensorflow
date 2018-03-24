/* Copyright 2018 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#ifndef TENSORFLOW_CONTRIB_TENSORRT_CONVERT_TRT_OPTIMIZATION_PASS_H_
#define TENSORFLOW_CONTRIB_TENSORRT_CONVERT_TRT_OPTIMIZATION_PASS_H_

#include <set>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "tensorflow/core/framework/graph.pb.h"
#include "tensorflow/core/grappler/optimizers/custom_graph_optimizer.h"
#include "tensorflow/core/platform/logging.h"

#if GOOGLE_CUDA
#if GOOGLE_TENSORRT

namespace tensorflow {
namespace tensorrt {
namespace convert {
    class TRTOptimizationPass:public tensorflow::grappler::CustomGraphOptimizer{
        public:
        TRTOptimizationPass(string optName="TRTOptimizationPass"):m_name_(optName){
          VLOG(0)<<"Constructing "<<m_name_;
        };
        //tensorflow::Status Run(const tensorflow::GraphOptimizationPassOptions &options) override;
        string name() const override {return m_name_;};
        tensorflow::Status Init() override {
          VLOG(0)<<"Called INIT"<<m_name_;
          return tensorflow::Status::OK();};
        tensorflow::Status Optimize(tensorflow::grappler::Cluster* cluster, const tensorflow::grappler::GrapplerItem& item,
        GraphDef* optimized_graph) override;
        void Feedback(tensorflow::grappler::Cluster* cluster, const tensorflow::grappler::GrapplerItem& item,
        const GraphDef& optimized_graph,double result) override;
        private:
        string m_name_;
    };
}
}
}
#endif
#endif
#endif